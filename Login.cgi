#!/usr/bin/perl 
use CGI;
use DBI;
use strict;
use warnings;
use CGI::Session;

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

#assign age group
my $AgeGroup = "1";
if ($Age>=18) {
    $AgeGroup = "1,2,3";
} elsif (($Age<18) && ($Age>=13)) {
    $AgeGroup = "1,2";    
}

#if user/pwd is correct login
if ($userID){
    #If Login is correct Set Cookies and create session
    my $cookie = $cgi->cookie(-name=>'MY_COOKIE',
			 -value=>'COOKIE_NAME=gameopedia',
			 -expires=>'+4h',
			 -path=>'/');
    print $cgi->header(-cookie=>$cookie);

    my $s = CGI::Session->new($cgi);

#Fetch User Games based on preferences
    my $data = qq{SELECT G.Id, G.Game_Name, G.Url from Games G where G.Target_Age_Group in (?) and G.Game_Theme in (?) and G.Game_Genre in (?) and G.Game_Violence in (?)};
    my $sth1 = $dbh->prepare($data)
    or die $dbh->errstr;
    $sth1->execute($AgeGroup,$Theme,$Genre,$Violence)
    or die $sth1->errstr;

#Display Games List
    print $cgi->start_html(
            -title      => 'Gameopedia Home Page',
            -style      => {'src'=>'/styles/style.css'},
    );
    

    print "<b> Games Suggested for you...</b><br><form method=post name=\"Addcart\" action=\"AddCart.cgi\">";
    while ( my @row = $sth1->fetchrow_array) {
        my $Id = $row[0];
        my $Game = $row[1];
        my $Url = $row[2];
        print "Game: $Game <br>";
        print "Url: <a href=$Url target=_blank>$Url</a> <br>";
        print "<input type=hidden name=\"game".$Id."\" value=\"".$Game."\">";
        print "<button type=\"submit\" name=\"add\">Add To Cart</button>";
    }
    print "</form>";
    print "<form action=\"logout.cgi/".$cgi."\" method=\"post\">"; 
    print "<button type=\"submit\" name=\"logout\">Logout</button>";
    print $cgi->end_html;


} else {
#Incorrect login redirect to login page again.
	my $url = "login.html";
	print "Location: $url\n\n";

}
