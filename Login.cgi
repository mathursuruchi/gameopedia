#!/usr/bin/perl 
use CGI;
use DBI;
use strict;
use warnings;
 
# read the CGI params
my $cgi = CGI->new;
my $username = $cgi->param("username");
my $password = $cgi->param("password");
 
# connect to the database
my $dbh = DBI->connect("DBI:mysql:database=;host=;port=", "", "") 
  or die $DBI::errstr;
 
# validate the username and password
my $statement = qq{SELECT Id,Age,Pref_Game_Theme,Pref_Game_Genre,Pref_Game_Violence FROM User WHERE User_Name=? and Password=?};
my $sth = $dbh->prepare($statement)
  or die $dbh->errstr;
$sth->execute($username, $password)
  or die $sth->errstr;
my ($userID,$Age,$Theme,$Genre,$Violence) = $sth->fetchrow_array;

my $AgeGroup = "1";
if ($Age>=18) {
    $AgeGroup = "1,2,3";
} elsif (($Age<18) && ($Age>=13)) {
    $AgeGroup = "1,2";    
}

if ($userID){
    #If Login is correct Set Cookies
    my $cookie = $cgi->cookie(-name=>'MY_COOKIE',
			 -value=>'COOKIE_NAME=gameopedia',
			 -expires=>'+4h',
			 -path=>'/');
    print $cgi->header(-cookie=>$cookie);

#Fetch User Games based on preferences
    my $data = qq{SELECT G.Game_Name from Games G where G.Target_Age_Group in (?) and G.Game_Theme in (?) and G.Game_Genre in (?) and G.Game_Violence in (?)};

    my $sth1 = $dbh->prepare($data)
    or die $dbh->errstr;
    $sth1->execute($AgeGroup,$Theme,$Genre,$Violence)
    or die $sth1->errstr;

#Display Games List
    print $cgi->start_html(
            -title      => 'gameopedia',
            -style      => {'src'=>'/styles/style.css'},
    );
    

    print "<b> Games Suggested for you...</b><br>";
    while ( my @row = $sth1->fetchrow_array) {
        my $Game = $row[0];
        my $Url = $row[1];
        print "Game: $Game <br>";
        print "Url: <a href=$Url target=_blank>$Url</a> <br>";
        print "<Input type=\"button\" Name=\"Add To Cart\">";
    }
    print $cgi->end_html;


} else {
#Incorrect login redirect to login page again.
	$url = "login.html";
	print "Location: $url\n\n";

}
